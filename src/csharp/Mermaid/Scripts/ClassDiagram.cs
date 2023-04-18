
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.MSBuild;

namespace Mermaid.Scripts;

public class ClassDiagram
{
    public readonly string solutionPath;

    public string outputFile;

    public ClassDiagram(string solutionPath, string outputFile)
    {
        this.solutionPath = solutionPath;
        this.outputFile = outputFile;
    }

    public void DumpSyntaxTree(SyntaxTree tree)
    {
        // Dump the syntax tree to the console
        Console.WriteLine(tree.ToString());
    }

    //public async Task DumpMermaid(IReadOnlyList<string> args)
    public async Task DumpMermaid()
    {
        // var solutionPath = args[0];
        // var outputFile = args[1];

        // outputFile = outputFile.Replace(
        //     Path.GetFileNameWithoutExtension(outputFile),
        //     Path.GetFileNameWithoutExtension(outputFile) + " Mermaid");

        //Path.Combine(Path.GetFileNameWithoutExtension(outputFile) + " Mermaid.mmd", outputFile);

        var directory = solutionPath; //Path.GetDirectoryName(solutionPath);

        Console.WriteLine($"Dump Mermaid Solution Path: {solutionPath}");
        Console.WriteLine($"Dump Mermaid Output File: {outputFile}");
        Console.WriteLine($"Dump Mermaid Directory: {directory}");

        if (!Directory.Exists(directory))
        {
            Console.WriteLine($"{directory} does not exist");
            return;
        }

        var relationships = new List<Tuple<string, string>>();
        var scriptCount = 0;

        foreach (var file in Directory.GetFiles(directory, "*.cs", SearchOption.AllDirectories))
        {
            if (file.Contains(".meta"))
                continue;

            relationships.AddRange(ParseCSharpCode(file));

            scriptCount++;

            await Task.Yield();
        }

        await Task.Yield();

        var mermaidScript = GenerateMermaidScript(relationships);

        File.WriteAllText(outputFile, mermaidScript);

        var referenceCount = relationships.Count;
        var uniqueClasses = relationships.Select(r => r.Item2).Distinct().Count();

        Console.WriteLine("Mermaid script has been generated as output.mmd");
        Console.WriteLine("Statistics:");
        Console.WriteLine($"  - Script count: {scriptCount}");
        Console.WriteLine($"  - Reference count: {referenceCount}");
        Console.WriteLine($"  - Unique classes referenced: {uniqueClasses}");
    }

    // public async Task DumpDependencies(IReadOnlyList<string> args)
    public async Task DumpDependencies()
    {
        try
        {
            // var solutionPath = args[0];
            // var outputFile = args[1];

            Console.WriteLine($"Solution Path: {solutionPath}");
            Console.WriteLine($"Output File: {outputFile}");

            await DumpMermaid();

            var projectFilePaths = await GetProjectFilePaths(solutionPath);

            var workspace = MSBuildWorkspace.Create(new Dictionary<string, string>()
            {
                { solutionPath, outputFile }
            });

            using var writer = new StreamWriter(outputFile, true);

            foreach (var projectFilePath in projectFilePaths)
            {
                Console.WriteLine($"Project File Path: {projectFilePath}");

                var project = await workspace.OpenProjectAsync(projectFilePath);

                Console.WriteLine(project);
                Console.WriteLine(project.Documents);

                var compilation = await project.GetCompilationAsync();

                if (compilation != null)
                {
                    Console.WriteLine(compilation);
                    Console.WriteLine(compilation.SyntaxTrees);
                }
                else
                {
                    Console.WriteLine($"Compilation is null at {projectFilePath}");
                    continue;
                }

                foreach (var syntaxTree in compilation.SyntaxTrees)
                {
                    Console.WriteLine($"Syntax Tree: {syntaxTree}");
                    var semanticModel = compilation.GetSemanticModel(syntaxTree);

                    var classDeclarations = (await syntaxTree.GetRootAsync()).DescendantNodes()
                        .OfType<ClassDeclarationSyntax>();

                    foreach (var classDeclaration in classDeclarations)
                    {
                        Console.WriteLine($"Class Declaration: {classDeclaration}");

                        var classSymbol = semanticModel.GetDeclaredSymbol(classDeclaration);

                        if (classSymbol == null)
                        {
                            Console.WriteLine($"Class symbol is null at {classDeclaration}");
                            continue;
                        }

                        var baseType = classSymbol.BaseType;

                        if (baseType != null)
                        {
                            await writer.WriteLineAsync($"{classSymbol.Name} --> {baseType.Name}");
                        }
                        else
                        {
                            Console.WriteLine($"Base type is null at {classDeclaration}");
                        }

                        var interfaces = classSymbol.Interfaces;
                        // if (interfaces == null)
                        // {
                        //     Console.WriteLine($"Interfaces is null at {classDeclaration}");
                        //     continue;
                        // }

                        foreach (var interfaceSymbol in interfaces)
                        {
                            await writer.WriteLineAsync($"{classSymbol.Name} --> {interfaceSymbol.Name}");
                        }
                    }
                }
            }

            // Console.WriteLine("\nContinue");
            // Console.ReadKey();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }

    public async Task<List<string>> GetProjectFilePaths(string solutionPath)
    {
        var projectFilePaths = new List<string>();

        using (var reader = new StreamReader(solutionPath))
        {
            string line;
            while ((line = await reader.ReadLineAsync()) != null)
            {
                // Are we assuming that the project file paths are always on the same line as the project name?
                if (line.StartsWith("Project("))
                {
                    var parts = line.Split(',');
                    if (parts.Length > 1)
                    {
                        var projectFilePath = parts[1].Trim().Trim('"');
                        projectFilePaths.Add(Path.Combine(Path.GetDirectoryName(solutionPath), projectFilePath));
                    }
                }
            }
        }

        return projectFilePaths;
    }

    // public async Task Main(string[] args)
    // {
    //     await DumpDependencies(new[]
    //     {
    //         "C:\\Apps\\WinPyTools\\src\\csharp\\Mermaid\\Mermaid.sln",
    //         "C:\\Apps\\WinPyTools\\test.txt"
    //     });

    //     await DumpDependencies(new[]
    //     {
    //         "C:\\Apps\\ModernTradingBot\\ModernCryptoBot.sln",
    //         "C:\\Apps\\WinPyTools\\test.txt"
    //     });

    //     await DumpDependencies(new[]
    //     {
    //         "C:\\Apps\\The-Prophecy-of-Hank\\HandyHank\\HandyHank.sln",
    //         "C:\\Apps\\WinPyTools\\test.txt"
    //     });
    // }

    public List<Tuple<string, string>> ParseCSharpCode(string filePath)
    {
        var relationships = new List<Tuple<string, string>>();

        var code = File.ReadAllText(filePath);
        var tree = CSharpSyntaxTree.ParseText(code);
        var root = tree.GetCompilationUnitRoot();

        var classDeclarations = root.DescendantNodes().OfType<ClassDeclarationSyntax>();

        foreach (var classDeclaration in classDeclarations)
        {
            var className = classDeclaration.Identifier.ToString();

            if (classDeclaration.BaseList != null)
                foreach (var baseType in classDeclaration.BaseList.Types)
                    relationships.Add(new Tuple<string, string>(className, baseType.ToString()));
        }

        return relationships;
    }

    public string GenerateMermaidScript(List<Tuple<string, string>> relationships)
    {
        var mermaidScript = "classDiagram\n";

        foreach (var relationship in relationships)
        {
            var className1 = relationship.Item1.Replace("<", "&lt;").Replace(">", "&gt;");
            var className2 = relationship.Item2.Replace("<", "&lt;").Replace(">", "&gt;");
            mermaidScript += $"    \"{className1}\" --|> \"{className2}\"\n";
        }

        return mermaidScript;
    }
}