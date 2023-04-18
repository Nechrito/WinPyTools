using System;
using System.Text.RegularExpressions;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.MSBuild;

namespace Mermaid.Scripts;

class FolderStructureOptimizer
{
    public FolderStructureOptimizer(string solutionPath, string outputFile)
    {
        this.solutionPath = solutionPath;
        this.outputFile = outputFile;
    }

    public string solutionPath { get; }
    public string outputFile { get; private set; }

    public void DumpSyntaxTree(SyntaxTree tree)
    {
        // Dump the syntax tree to the console
        Console.WriteLine(tree.ToString());
    }

    private static string ParseClassParameters(ClassDeclarationSyntax classDeclaration)
    {
        var constructor = classDeclaration.DescendantNodes().OfType<ConstructorDeclarationSyntax>().FirstOrDefault();

        if (constructor != null)
        {
            var parameters = constructor.ParameterList.Parameters;
            return string.Join(", ", parameters);
        }

        return string.Empty;
    }

    private List<Tuple<string, string, string>> ParseCSharpCode(string file)
    {
        var relationships = new List<Tuple<string, string, string>>();
        var tree = CSharpSyntaxTree.ParseText(File.ReadAllText(file));
        var root = tree.GetRoot();
        var classes = root.DescendantNodes().OfType<ClassDeclarationSyntax>();

        foreach (var @class in classes)
        {
            var baseList = @class.BaseList;

            if (baseList != null)
            {
                foreach (var type in baseList.Types)
                {
                    var baseClass = type.Type.ToString();
                    var classParameters = ParseClassParameters(@class);

                    if (@class.Identifier.Text.Contains('@'))
                    {
                        continue;
                    }

                    baseClass = baseClass.Replace('<', '[').Replace('>', ']');

                    baseClass = Regex.Replace(baseClass, @"(.*)\[(.*)\]", "$1");

                    baseClass = Regex.Replace(baseClass, @"(.*)\[(.*)", "$1");

                    if (baseClass == "MonoBehaviour" || baseClass == "ScriptableObject" || baseClass == "SerializedScriptableObject" || baseClass == "SerializedMonoBehaviour")
                    {
                        baseClass = string.Empty;
                    }

                    relationships.Add(new Tuple<string, string, string>(@class.Identifier.Text, baseClass, classParameters));
                }
            }
        }

        return relationships;
    }

    public void FindOptimalFolderStructure()
    {
        var all_relationships = new List<Tuple<string, string, string>>();

        // Traverse the syntax tree to analyze relationships and classify classes
        var files = Directory.GetFiles(solutionPath, "*.cs", SearchOption.AllDirectories);

        foreach (var file in Directory.GetFiles(solutionPath, "*.cs", SearchOption.AllDirectories))
        {
            if (file.Contains(".meta"))
                continue;

            all_relationships.AddRange(ParseCSharpCode(file));
        }

        var syntaxTrees = files.Select(file => CSharpSyntaxTree.ParseText(File.ReadAllText(file))).ToArray();
        var references = new MetadataReference[] { MetadataReference.CreateFromFile(typeof(object).Assembly.Location) };
        var compilation = CSharpCompilation.Create("Temp", syntaxTrees, references);

        Dictionary<string, string> classToFolderMap = new();

        // Iterate through syntax trees
        foreach (var tree in syntaxTrees)
        {
            var semanticModel = compilation.GetSemanticModel(tree);

            var root = tree.GetCompilationUnitRoot();

            //var relationships = ParseCSharpCode() //ParseCSharpCode(files.FirstOrDefault(file => file.Contains(root.DescendantNodes().OfType<ClassDeclarationSyntax>().FirstOrDefault().Identifier.Text + ".cs")));

            // Find all class declarations
            var classDeclarations = root.DescendantNodes().OfType<ClassDeclarationSyntax>();

            // Iterate through class declarations and classify each class
            foreach (var classDeclaration in classDeclarations)
            {
                var classSymbol = semanticModel.GetDeclaredSymbol(classDeclaration);

                var className = classSymbol.Name;

                all_relationships.Where(r => r.Item1 == className).ToList().ForEach(r => all_relationships.Add(new Tuple<string, string, string>(className, r.Item2, r.Item3)));

                // Generate a folder for each class by it's relationship with other classes in the solution
                var folderName = string.Empty;

                if (all_relationships.Any(r => r.Item1 == className && r.Item2 != string.Empty))
                {
                    var baseClass = all_relationships.FirstOrDefault(r => r.Item1 == className && r.Item2 != string.Empty).Item2;

                    folderName = baseClass;
                }
                else
                {
                    folderName = "Misc";
                }

                classToFolderMap[className] = folderName;
            }
        }

        // Iterate through the classified classes and move each class to its designated folder.
        foreach (var classToFile in classToFolderMap)
        {
            var className = classToFile.Key;
            var folderName = classToFile.Value;
            var sourceFilePath = files.FirstOrDefault(file => file.Contains(className + ".cs"));
            var destinationFolderPath = Path.Combine(solutionPath, folderName);

            // Create the destination folder if it doesn't exist
            if (!Directory.Exists(destinationFolderPath))
            {
                Directory.CreateDirectory(destinationFolderPath);
            }

            var destinationFilePath = Path.Combine(destinationFolderPath, className + ".cs");

            Console.WriteLine($"Moving {className} to {destinationFilePath}");

            //File.Move(sourceFilePath, destinationFilePath);
        }
    }
}